"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import * as z from "zod";
import { CalendarIcon, Send } from "lucide-react";
import { format } from "date-fns";

import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Calendar } from "@/components/ui/calendar";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { cn } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const formSchema = z.object({
  facility_id: z
    .string()
    .length(4, "Facility ID must be exactly 4 characters")
    .regex(/^[A-Z0-9]{4}$/, "Must be a 4-character ICAO/IATA code")
    .transform((val) => val.toUpperCase()),
  status_type: z.string().min(1, "Please select a status type"),
  raw_notam_text: z.string().min(5, "Details must be at least 5 characters"),
  timestamp_utc: z.date({
    message: "A valid timestamp is required",
  }),
});

export default function AdminPage() {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      facility_id: "",
      status_type: "",
      raw_notam_text: "",
      timestamp_utc: new Date(),
    },
  });

  function onSubmit(values: z.infer<typeof formSchema>) {
    // In a real app, this would POST to /api/v1/status
    console.log("Submitting Status Report:", values);
    alert("Report Submitted (Check Console for Payload)");
  }

  return (
    <div className="min-h-screen bg-atc-background text-foreground p-8 flex items-center justify-center">
      <Card className="w-full max-w-lg bg-atc-card border-slate-700">
        <CardHeader>
          <CardTitle className="text-2xl font-bold text-white flex items-center gap-2">
            <span className="text-primary">Admin</span> Manual Entry
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              
              {/* Facility ID */}
              <FormField
                control={form.control}
                name="facility_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-slate-300">Facility ID (ICAO)</FormLabel>
                    <FormControl>
                      <Input 
                        placeholder="KORD" 
                        {...field} 
                        className="bg-slate-900 border-slate-700 text-white font-mono uppercase placeholder:text-slate-600"
                        maxLength={4}
                      />
                    </FormControl>
                    <FormDescription className="text-xs text-slate-500">
                      Standard 4-letter identifier.
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Status Type */}
              <FormField
                control={form.control}
                name="status_type"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-slate-300">Status Type</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger className="bg-slate-900 border-slate-700 text-white">
                          <SelectValue placeholder="Select status..." />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent className="bg-slate-900 border-slate-700 text-white">
                        <SelectItem value="NORMAL_OPS">NORMAL OPS</SelectItem>
                        <SelectItem value="RUNWAY_CLOSURE">RUNWAY CLOSURE</SelectItem>
                        <SelectItem value="DEICING">DEICING ALERT</SelectItem>
                        <SelectItem value="CAUTION">CAUTION / DELAY</SelectItem>
                        <SelectItem value="ATC_ZERO">ATC ZERO (EVAC)</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Timestamp */}
              <FormField
                control={form.control}
                name="timestamp_utc"
                render={({ field }) => (
                  <FormItem className="flex flex-col">
                    <FormLabel className="text-slate-300">Timestamp (UTC)</FormLabel>
                    <Popover>
                      <PopoverTrigger asChild>
                        <FormControl>
                          <Button
                            variant={"outline"}
                            className={cn(
                              "w-full pl-3 text-left font-normal bg-slate-900 border-slate-700 text-white hover:bg-slate-800 hover:text-white",
                              !field.value && "text-muted-foreground"
                            )}
                          >
                            {field.value ? (
                              format(field.value, "PPP HH:mm")
                            ) : (
                              <span>Pick a date</span>
                            )}
                            <CalendarIcon className="ml-auto h-4 w-4 opacity-50" />
                          </Button>
                        </FormControl>
                      </PopoverTrigger>
                      <PopoverContent className="w-auto p-0 bg-slate-900 border-slate-700" align="start">
                        <Calendar
                          mode="single"
                          selected={field.value}
                          onSelect={field.onChange}
                          disabled={(date) =>
                            date > new Date() || date < new Date("1900-01-01")
                          }
                          initialFocus
                          className="text-white"
                        />
                      </PopoverContent>
                    </Popover>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Details / RAW NOTAM */}
              <FormField
                control={form.control}
                name="raw_notam_text"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-slate-300">Report Details</FormLabel>
                    <FormControl>
                      <Input 
                        placeholder="RWY 27R CLOSED DUE TO SNOW REMOVAL" 
                        {...field} 
                        className="bg-slate-900 border-slate-700 text-white font-mono placeholder:text-slate-600"
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <Button type="submit" className="w-full bg-primary hover:bg-primary/90 text-primary-foreground font-semibold">
                <Send className="mr-2 h-4 w-4" /> Submit Report
              </Button>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  );
}
